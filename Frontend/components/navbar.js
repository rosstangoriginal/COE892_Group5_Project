"use client"

import { useRouter } from 'next/navigation';

import Link from "next/link"
import {
  CircleUser,
  Wallet,
} from "lucide-react"

import { Button } from "@/components/ui/button"

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

function Navbar() {

    const router = useRouter();

    const handleLogout = () => {
        localStorage.removeItem('user_id');
        router.push('/login');
    };

    return(

    <header className="sticky top-0 flex h-16 items-center gap-4 border-b bg-background px-4 md:px-6">
        <nav className="hidden flex-col gap-6 text-lg font-medium md:flex md:flex-row md:items-center md:gap-5 md:text-sm lg:gap-6">
          <Link
                href="/"
                className="flex items-center gap-2 text-lg font-semibold md:text-base"
            >
                <Wallet className="h-6 w-6" />
                <span className="sr-only"></span>
            </Link>
            <Link
                href="/"
                className="text-foreground transition-colors hover:text-foreground"
            >
                Dashboard
            </Link>
            <Link
                href="/assets"
                className="text-muted-foreground transition-colors hover:text-foreground"
            >
                Assets
            </Link>
            <Link
                href="/transactions"
                className="text-muted-foreground transition-colors hover:text-foreground"
            >
                Transactions
            </Link>
        </nav>
        <div className="ml-auto">
             <DropdownMenu>
                 <DropdownMenuTrigger asChild>
                 <Button variant="secondary" size="icon" className="rounded-full">
                     <CircleUser className="h-5 w-5" />
                     <span className="sr-only">Toggle user menu</span>
                 </Button>
                 </DropdownMenuTrigger>
                 <DropdownMenuContent align="end">
                 <DropdownMenuItem onClick={handleLogout}>Logout</DropdownMenuItem>
                 </DropdownMenuContent>
             </DropdownMenu>
         </div>
      </header>
    )
  }
  
  export default Navbar;