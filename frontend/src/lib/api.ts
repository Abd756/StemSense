import axios from 'axios';

const NEXT_PUBLIC_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
    baseURL: NEXT_PUBLIC_API_URL,
});

export const submitTask = async (input: string) => {
    const formData = new FormData();
    formData.append('input', input);
    const response = await api.post('/process', formData);
    return response.data;
};

export const getTaskStatus = async (taskId: string) => {
    const response = await api.get(`/tasks/${taskId}`);
    return response.data;
};

export const getDownloadUrl = (filename: string) => {
    return `${NEXT_PUBLIC_API_URL}/download/${filename}`;
};
