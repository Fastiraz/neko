import PocketBase from 'pocketbase';

const pb = new PocketBase('http://127.0.0.1:8090');

export async function login(email: string, password: string) {
  try {
    const authData = await pb.collection('users').authWithPassword(email, password);
    return {
      token: pb.authStore.token,
      user: pb.authStore.model,
    };
  } catch (error) {
    throw new Error('Invalid credentials');
  }
}

export function logout() {
  pb.authStore.clear();
}

export function isAuthenticated() {
  return pb.authStore.isValid;
}

export function getCurrentUser() {
  return pb.authStore.model;
}
