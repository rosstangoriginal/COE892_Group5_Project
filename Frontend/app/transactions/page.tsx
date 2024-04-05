"use client"

import {AllTransactions} from "@/components/transaction-table"
import Navbar from "@/components/navbar";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

// Call this function on every page where you need to protect the route
const redirectToLoginIfNotAuthenticated = () => {
  const router = useRouter();

  useEffect(() => {
    const userId = localStorage.getItem('user_id');

    if (!userId) {
      router.push('/login');
    }
  }, [router]);
};

export default function Transactions() {
  redirectToLoginIfNotAuthenticated();
  return (
    <>
    <Navbar />
    <AllTransactions />
    </>
  );
}