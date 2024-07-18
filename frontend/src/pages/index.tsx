import { encryptWithPublicKey, verifyAttestationDoc } from "@/lib/attestation";
import { Inter } from "next/font/google";
import { useState } from "react";
import { toast } from "sonner";

const inter = Inter({ subsets: ["latin"] });

const SERVER_URL = "http://18.222.167.165";

export default function Home() {
  const [publicKey, setPublicKey] = useState<string | null>(null);
  const [input, setInput] = useState<string>("");

  const getEnclavePublicKey = async () => {
    const response = await fetch(`${SERVER_URL}/get-enclave-key`);
    const data = await response.json();
    const publicKey = await verifyAttestationDoc(data.attestation_doc);
    setPublicKey(publicKey);
  };

  const encryptAndSendData = async () => {
    if (!publicKey) {
      toast.error("Must get public key first!");
      return;
    }

    if (!input) {
      toast.error("Must input data to send!");
      return;
    }

    const encryptedData = encryptWithPublicKey(publicKey, input);
    const response = await fetch(`${SERVER_URL}/send-encrypted-data`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ data: encryptedData }),
    });

    if (response.ok) {
      toast.success("Data sent successfully!");
    } else {
      toast.error("Failed to send data!");
    }
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

      {publicKey && (
        <div className="bg-gray-500 p-4 mt-4 rounded-md">
          <pre>{publicKey}</pre>
        </div>
      )}

      <input
        type="text"
        placeholder="Insert data..."
        className="border p-2 mt-4 w-1/2 rounded-md text-black"
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <button
        className="bg-purple-500 p-4 mt-4 rounded-md"
        onClick={encryptAndSendData}
      >
        Encrypt and Send Data to Enclave
      </button>
    </main>
  );
}
