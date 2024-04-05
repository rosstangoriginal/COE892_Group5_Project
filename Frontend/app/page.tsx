"use client"

import Link from "next/link"
import {
  ArrowUpRight,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

import SimpleLineChart from "@/components/line-chart"
import { RecentTransactions } from "@/components/transaction-table"
import { AssetsGlance } from "@/components/assets-table"
import Navbar from "@/components/navbar"

import { useState, useEffect } from 'react';
import axios from 'axios';

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

export default function Dashboard() {

  const api_url = process.env.NEXT_PUBLIC_API_URL;
  const [portfolioValue, setPortfolioValue] = useState('Loading...');
  const [pl, setPL] = useState('Loading...');
  
  const fetchPortfolioValue = async () => {
    try {
      const userId = localStorage.getItem('user_id');
      const portfolioResponse = await axios.get(`${api_url}/portfolios/get_portfolio/${userId}`);
      const portfolioId = portfolioResponse.data.PortfolioID;
      const response = await axios.get(`${api_url}/portfolios/get_total_portfolio_value/${portfolioId}`);
      setPortfolioValue(response.data.PortfolioValue);
      setPL(response.data.PL);
    } catch (error) {
      console.error('There was an error fetching the portfolio value', error);
      setPortfolioValue('0');
      setPL('0')
    }
  };

  useEffect(() => {
    fetchPortfolioValue();
  }, []);

  redirectToLoginIfNotAuthenticated();

  return (
    <>
    <Navbar />
    <div className="flex min-h-screen w-full flex-col">
      <main className="flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-8">
        <div className="grid gap-4 md:grid-cols-2 md:gap-8 lg:grid-cols-4">
            <Card className="xl:col-span-2">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Portfolio Value
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">${portfolioValue}</div>
                <p className={`text-xs ${parseFloat(pl) < 0 ? 'text-red-500' : 'text-green-500'}`}>
                  ${pl}
                </p>
                <SimpleLineChart />
              </CardContent>
            </Card>
        </div>
        <div className="grid gap-4 md:gap-8 lg:grid-cols-2 xl:grid-cols-3">
          <Card className="xl:col-span-2">
            <CardHeader className="flex flex-row items-center">
              <div className="grid gap-2">
                <CardTitle>Recent Transactions</CardTitle>
                <CardDescription>
                  Recent transactions from your portfolio.
                </CardDescription>
              </div>
              <Button asChild size="sm" className="ml-auto gap-1">
                <Link href="/transactions">
                  View All
                  <ArrowUpRight className="h-4 w-4" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent>
              <RecentTransactions />
            </CardContent>
          </Card>
          <Card className="xl:col-span-2">
            <CardHeader className="flex flex-row items-center">
              <div className="grid gap-2">
                <CardTitle>Your assets</CardTitle>
                <CardDescription>
                  At a glance.
                </CardDescription>
              </div>
              <Button asChild size="sm" className="ml-auto gap-1">
                <Link href="/assets">
                  View All
                  <ArrowUpRight className="h-4 w-4" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent>
              <AssetsGlance />
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
    </>
  )
}
