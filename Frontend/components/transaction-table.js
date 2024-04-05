"use client"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { useEffect, useState } from "react";
import axios from 'axios';

const RecentTransactions = () => {

  const api_url = process.env.NEXT_PUBLIC_API_URL;

  const [recentTransactions, setRecentTransactions] = useState([]);

  useEffect(() => {
    const fetchRecentTransactions = async () => {

      const user_id = localStorage.getItem('user_id');

      if (!user_id) {
        console.error('User ID not found');
        return;
      }

      try {
        const response = await axios.get(`${api_url}/transactions/get_last_five_transactions/${user_id}`);
        console.log(response.data);
        setRecentTransactions(response.data);
      } catch (error) {
        console.error('Failed to fetch transactions:', error);
      }
    };

    fetchRecentTransactions();
  }, [api_url]);

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Asset</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Quantity</TableHead>
          <TableHead>Price</TableHead>
          <TableHead>Date</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {recentTransactions.map((transaction) => (
          <TableRow key={transaction.TransactionID}>
            <TableCell>
              {transaction.AssetName}
            </TableCell>
            <TableCell>{transaction.TransactionType}</TableCell>
            <TableCell>
              {transaction.Quantity}
            </TableCell>
            <TableCell>
              {transaction.TransactionPrice}
            </TableCell>
            <TableCell>{transaction.TransactionDate}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
};

const AllTransactions = () => {

  const api_url = process.env.NEXT_PUBLIC_API_URL;

  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    const fetchTransactions = async () => {

      const user_id = localStorage.getItem('user_id');

      if (!user_id) {
        console.error('User ID not found');
        return;
      }

      try {
        const response = await axios.get(`${api_url}/transactions/get_user_transactions/${user_id}`);
        console.log(response.data);
        setTransactions(response.data);
      } catch (error) {
        console.error('Failed to fetch transactions:', error);
      }
    };

    fetchTransactions();
  }, [api_url]);

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Asset</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Quantity</TableHead>
          <TableHead>Price</TableHead>
          <TableHead>Date</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {transactions.map((transaction) => (
          <TableRow key={transaction.TransactionID}>
            <TableCell>
              {transaction.AssetName}
            </TableCell>
            <TableCell>{transaction.TransactionType}</TableCell>
            <TableCell>
              {transaction.Quantity}
            </TableCell>
            <TableCell>
              {transaction.TransactionPrice}
            </TableCell>
            <TableCell>{transaction.TransactionDate}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
};

export {RecentTransactions, AllTransactions};