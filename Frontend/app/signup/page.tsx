"use client"

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import axios from 'axios';

import Link from "next/link"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

const getTodayDate = () => {
  const today = new Date();
  const month = `0${today.getMonth() + 1}`.slice(-2); 
  const day = `0${today.getDate()}`.slice(-2);
  return `${today.getFullYear()}-${month}-${day}`;
};

export default function SignupForm() {

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const router = useRouter();

  const api_url = process.env.NEXT_PUBLIC_API_URL;

  const handleSignup = async () => {
    let userId = null;
  
    try {
      const createUserResponse = await axios.post(`${api_url}/users/create_user`, {
        username: username,
        email: email,
        password: password,
      });
  
      // Assuming the user creation response contains the ID in the `data` object directly
      userId = createUserResponse.data;
  
      // Prepare the data for portfolio creation
      const portfolioData = {
        user_id: userId,
        portfolio_name: `Portfolio of ${username}`,
        description: `Portfolio of ${username}`,
        creation_date: getTodayDate(),
      };
  
      const createPortfolioResponse = await axios.post(`${api_url}/portfolios/create_portfolio`, portfolioData);
  
      if (createPortfolioResponse.status === 200) {
        router.push('/login'); // Redirect to login after successful signup and portfolio creation
      } else {
        throw new Error('Failed to create portfolio'); // This will be caught by the catch block below
      }
    } catch (error: any) {
      if (error.response?.status === 409) {
        setErrorMessage("Username is already taken");
      } else {
        if (userId) {
          // An error occurred after creating the user, delete the user
          try {
            await axios.delete(`${api_url}/users/delete_user/${userId}`);
            console.log(`User with ID: ${userId} was deleted after failed portfolio creation.`);
          } catch (deleteError: any) {
            console.error(`Failed to delete user with ID: ${userId}:`, deleteError.response?.data || deleteError.message);
          }
        }
        setErrorMessage('An error occurred during signup.');
      }
    }
  };
    
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
    <Card className="mx-auto max-w-sm">
      <CardHeader>
        <CardTitle className="text-xl">Sign Up</CardTitle>
        <CardDescription>
          Enter your information to create an account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="username">Username</Label>
              <Input id="username" placeholder="coe892goat" required value={username} onChange={(e) => {setUsername(e.target.value); setErrorMessage('');}}/>
            </div>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="email@torontomu.ca"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="password">Password</Label>
            <Input id="password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)}/>
          </div>
          {errorMessage && <div className="text-red-600">{errorMessage}</div>}
          <Button onClick={handleSignup} type="submit" className="w-full">
            Create an account
          </Button>
        </div>
        <div className="mt-4 text-center text-sm">
          Already have an account?{" "}
          <Link href="/login" className="underline">
            Sign in
          </Link>
        </div>
      </CardContent>
    </Card>
    </div>
  )
}