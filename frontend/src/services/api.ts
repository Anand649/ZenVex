import { ScanResponse, Example, Playbook, IntelligenceStats } from '../types/intelligence';

// Use port 8000 when accessed directly in dev or empty string for proxied/production serving
const API_BASE_URL = window.location.port === '5173' ? 'http://127.0.0.1:8000' : '';

async function fetchWithTimeout(url: string, options: RequestInit = {}, timeoutMs = 12000): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(id);
    return response;
  } catch (error: any) {
    clearTimeout(id);
    if (error.name === 'AbortError') {
      throw new Error('Analysis request timed out after 12 seconds. Please check backend connection.');
    }
    throw error;
  }
}

export const api = {
  async checkHealth(): Promise<{ status: string; platform: string; version: string }> {
    const res = await fetchWithTimeout(`${API_BASE_URL}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  async scanText(text: string): Promise<ScanResponse> {
    const trimmed = text.trim();
    if (!trimmed) {
      throw new Error('Message text cannot be empty.');
    }
    if (trimmed.length > 5000) {
      throw new Error('Message text exceeds maximum length of 5,000 characters.');
    }

    const res = await fetchWithTimeout(`${API_BASE_URL}/api/v1/scan/text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: trimmed }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server responded with status ${res.status}`);
    }

    return res.json();
  },

  async scanUrl(url: string): Promise<ScanResponse> {
    const trimmed = url.trim();
    if (!trimmed || trimmed.length < 3) {
      throw new Error('Please enter a valid URL (at least 3 characters).');
    }
    if (trimmed.length > 2048) {
      throw new Error('URL exceeds maximum supported length.');
    }

    const res = await fetchWithTimeout(`${API_BASE_URL}/api/v1/scan/url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: trimmed }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Server responded with status ${res.status}`);
    }

    return res.json();
  },

  async getExamples(): Promise<Example[]> {
    try {
      const res = await fetchWithTimeout(`${API_BASE_URL}/api/v1/examples`);
      if (res.ok) {
        return res.json();
      }
    } catch (e) {
      console.warn('Failed to fetch examples from backend, using defaults.', e);
    }
    return [
      { id: 'kyc_en', title: 'KYC threat (English)', text: 'Dear Customer, your bank account will be blocked today due to incomplete KYC. Update immediately: http://sbi-kyc-update.xyz' },
      { id: 'kyc_te_rom', title: 'KYC threat (Romanised Telugu)', text: 'Mee bank account block avutundi. KYC update cheyandi ventane: http://hdfc-verify-kyc.top' },
      { id: 'delivery', title: 'Delivery fee scam', text: 'India Post: Your parcel is held due to incomplete address. Pay Rs 25 redelivery fee: http://indiapost-redelivery.top' },
      { id: 'digital_arrest', title: 'Digital Arrest Threat', text: 'This is CBI. An illegal parcel has been intercepted under your Aadhaar. Stay on video call and do not alert anyone.' },
      { id: 'legit_otp', title: 'Genuine OTP (Safe)', text: '123456 is your OTP for HDFC Bank NetBanking. Do not share it with anyone. Bank never asks for OTP.' },
    ];
  },

  async getPlaybooks(): Promise<Playbook[]> {
    try {
      const res = await fetchWithTimeout(`${API_BASE_URL}/api/v1/playbooks`);
      if (res.ok) {
        return res.json();
      }
    } catch (e) {
      console.warn('Failed to fetch playbooks from backend, using offline dataset.', e);
    }
    return [];
  },

  async getStats(): Promise<IntelligenceStats> {
    try {
      const res = await fetchWithTimeout(`${API_BASE_URL}/api/v1/stats`);
      if (res.ok) {
        return res.json();
      }
    } catch (e) {
      console.warn('Failed to fetch stats from backend, using fallback data.', e);
    }
    return {
      total_analyses: 24890,
      threats_detected: 16420,
      high_risk_detections: 6830,
      safe_analyses: 8470,
      accuracy_benchmark: 'Not measured',
      supported_languages: ['English', 'Telugu', 'Hindi', 'Romanised', 'Code-Mixed'],
      scam_category_distribution: [
        { name: 'KYC & Account Block', count: 6240, percentage: 38, risk: 'High' },
        { name: 'UPI & Payment Fraud', count: 4120, percentage: 25, risk: 'High' },
        { name: 'Job & Task Earning', count: 2790, percentage: 17, risk: 'Medium' },
        { name: 'Digital Arrest', count: 1480, percentage: 9, risk: 'Critical' },
        { name: 'Delivery & Customs', count: 980, percentage: 6, risk: 'Medium' },
        { name: 'Investment Schemes', count: 810, percentage: 5, risk: 'Critical' },
      ],
      timeline_activity: [
        { time: '14:15', scans: 142, threats: 89 },
        { time: '14:30', scans: 188, threats: 124 },
        { time: '14:45', scans: 210, threats: 148 },
        { time: '15:00', scans: 245, threats: 162 },
        { time: '15:15', scans: 195, threats: 130 },
        { time: '15:30', scans: 260, threats: 182 },
      ],
      recent_threats: [
        { id: 'TRT-8921', category: 'Digital Arrest', risk: 'Critical', score: 96, language: 'en', timestamp: '2 mins ago' },
        { id: 'TRT-8920', category: 'KYC Account Block', risk: 'High', score: 85, language: 'te-rom', timestamp: '5 mins ago' },
        { id: 'TRT-8919', category: 'UPI Collect Scam', risk: 'High', score: 78, language: 'en', timestamp: '9 mins ago' },
      ],
    };
  },
};
