import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });

const SERVER_URL = "http://18.222.167.165";

export default function Home() {
  const getEnclavePublicKey = async () => {
    const response = await fetch(`${SERVER_URL}/get-enclave-key`);
    const data = await response.json();
    console.log(data.attestation_doc);
  };

  return (
    <main
      className={`flex min-h-screen flex-col bg-white items-center justify-between p-24 ${inter.className}`}
    >
      <button
        className="bg-purple-500 p-4 rounded-md"
        onClick={getEnclavePublicKey}
      >
        Get Enclave Public Key
      </button>
    </main>
  );
}
