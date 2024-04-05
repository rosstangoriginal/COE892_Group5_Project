"use client"

import { AssetsTable } from "@/components/assets-table"
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

export default function Assets() {
  redirectToLoginIfNotAuthenticated();
  return (
    <>
    <Navbar />
    <AssetsTable />
    </>
  );
}