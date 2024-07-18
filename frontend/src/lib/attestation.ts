import { decode } from "cbor-x";
import forge from "node-forge";

// This is the expected application PCR of the enclave image
const EXPECTED_PCR2 =
  "baf36266029f0601598640dd349f382a959d6894f3da87f4ae5c08f38e698889c64cd9e83cecaa72c27c8e4b84ace769";

// Decode an AWS Nitro attestation document, verify the PCR2 value and return the PEM encoded public key
export const verifyAttestationDoc = async (
  attestationDoc: string
): Promise<string> => {
  const data = decode(decodeBase64ToUint8Array(attestationDoc));
  const doc = decode(data[2]);
  console.log("Decoded attestation doc: ", doc);
  const { pcrs, public_key } = doc;

  // Display PCRs
  Object.entries(pcrs as Record<number, Uint8Array>).forEach(([index, pcr]) => {
    if (!pcr) throw new Error(`Wrong PCR${index}`);
    const docPcr = Buffer.from(pcr).toString("hex");
    console.log(`PCR${index}: ${docPcr}`);
  });

  // Ensure PCR2 exists and is equal to the expected
  const pcr2 = pcrs[2];
  if (!pcr2) throw new Error("PCR2 is missing");
  const docPcr2 = Buffer.from(pcr2).toString("hex");
  if (docPcr2 !== EXPECTED_PCR2) {
    throw new Error("PCR2 does not match the expected value");
  } else {
    console.log("PCR2 matches the expected value!");
  }

  // TODO: Verify certificate

  const publicKeyPem = forge.pki.publicKeyToPem(
    forge.pki.publicKeyFromAsn1(
      forge.asn1.fromDer(forge.util.createBuffer(public_key))
    )
  );

  return publicKeyPem;
};

export const encryptWithPublicKey = (
  publicKey: string,
  data: string
): string => {
  const publicKeyObj = forge.pki.publicKeyFromPem(publicKey);
  const encrypted = publicKeyObj.encrypt(data, "RSA-OAEP");

  return forge.util.encode64(encrypted);
};

const decodeBase64ToUint8Array = (base64: string): Uint8Array => {
  const binaryString = atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
};
