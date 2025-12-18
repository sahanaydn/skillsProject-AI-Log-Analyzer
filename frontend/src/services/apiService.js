import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';



export const uploadLogFile = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (err) {
        throw new Error(err.response?.data?.detail || 'An unexpected error occurred during file upload.');
    }
};

export const getSummary = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/summary`);
        return response.data;
    } catch (err) {
        throw new Error(err.response?.data?.detail || 'Failed to fetch summary.');
    }
};

export const postQuery = async (query) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/query`, { query }, {
            headers: {
                'Content-Type': 'application/json',
            },
        });
        return response.data;
    } catch (err) {
        throw new Error(err.response?.data?.detail || 'An error occurred while getting the chat response.');
    }
};
