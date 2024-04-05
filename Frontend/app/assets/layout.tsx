import "../globals.css";

interface RootLayoutProps {
  children: React.ReactNode
}

export default function CertificatesLayout({ children }: RootLayoutProps) {
  return <section>{children}</section>
}
