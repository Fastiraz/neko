export async function sendMessageToAgent(prompt: string): Promise<string> {
  const response = await fetch("http://localhost:1337/api/v1/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    throw new Error("Failed to get response from AI agent");
  }

  const data = await response.json();
  return data.response || "No reply from AI.";
}
