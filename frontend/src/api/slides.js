import axios from 'axios';

export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export async function fetchSlides() {
  const { data } = await client.get('/slides');
  return data;
}

export async function fetchSlideById(id) {
  const { data } = await client.get(`/slides/${id}`);
  return data;
}

export async function fetchSlideDzi(id) {
  const { data } = await client.get(`/slides/${id}/dzi`);
  return data;
}

export async function createSlide(payload) {
  const { data } = await client.post('/slides', payload);
  return data;
}
