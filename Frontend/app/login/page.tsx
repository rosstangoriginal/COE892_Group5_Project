"use client"

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import axios from 'axios';

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

import Link from "next/link"

export default function LoginForm() {

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('');

    const router = useRouter();

    const api_url = process.env.NEXT_PUBLIC_API_URL;

    function handleLogin(event: any) {
        event.preventDefault(); // To prevent form submission if you are using a form
        
        // Now call the async function and handle it inside
        async function attemptLogin() {
          try {
            const response = await fetch(`${api_url}/users/login`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                username: username,
                password: password
              })
            });
      
            if(response.status === 200){
                const user_id = await response.json();
                localStorage.setItem('user_id', user_id);
                console.log('Login successful, user_id saved to localStorage');
                router.push('/');
            }
            else if (response.status === 404) {//username not exist
                setErrorMessage("Username does not exist");
            } else if (response.status === 401) {//wrong password
                setErrorMessage("Wrong password");
            }
          } catch (error: any) {
            console.error('Signup failed:', error.response?.status || error.response?.detail);
          }
        }
      
        attemptLogin();
    }
    
    return (
        <div className="flex min-h-screen items-center justify-center bg-gray-100">
        <Card className="mx-auto max-w-sm">
            <CardHeader>
                <CardTitle className="text-2xl">Login</CardTitle>
                <CardDescription>
                Enter your email below to login to your account
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div className="grid gap-4">
                <div className="grid gap-2">
                    <Label htmlFor="email">Username</Label>
                    <Input
                    id="username"
                    type="text"
                    placeholder="coe892goat"
                    required
                    value={username}
                    onChange={(e) => {setUsername(e.target.value); setErrorMessage('');}}
                    />
                </div>
                <div className="grid gap-2">
                    <div className="flex items-center">
                    <Label htmlFor="password">Password</Label>
                    {/* <Link href="#" className="ml-auto inline-block text-sm underline">
                        Forgot your password?
                    </Link> */}
                    </div>
                    <Input id="password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)}/>
                </div>
                {errorMessage && <div className="text-red-600">{errorMessage}</div>}
                <Button type="submit" className="w-full" onClick={handleLogin}>
                    Login
                </Button>
                </div>
                <div className="mt-4 text-center text-sm">
                Don&apos;t have an account?{" "}
                <Link href="/signup" className="underline">
                    Sign up
                </Link>
                </div>
            </CardContent>
        </Card>
        </div>
  )
}