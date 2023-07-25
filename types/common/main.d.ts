interface Message {
  text: string;
  sender: string;
}

type VerificationDetails = {
  messages: string;
  signature: string;
};

interface Verified {
  verified: boolean;
}
