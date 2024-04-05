"use client"

import React, { useState, useEffect } from 'react';
import axios from 'axios'; // Make sure to install axios if you haven't already
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

const SimpleLineChart = () => {

  const api_url = process.env.NEXT_PUBLIC_API_URL;
  const [performanceData, setPerformanceData] = useState([]);

  useEffect(() => {
    const fetchPerformanceData = async () => {
      try {
        const userId = localStorage.getItem('user_id');
        const portfolioResponse = await axios.get(`${api_url}/portfolios/get_portfolio/${userId}`);
        const portfolioId = portfolioResponse.data.PortfolioID;
        const response = await axios.get(`${api_url}/performance/by_portfolioid/${portfolioId}`);
        setPerformanceData(response.data);
      } catch (error) {
        console.error('Error fetching performance data:', error);
        // Handle error or set some state to show an error message
      }
    };

    fetchPerformanceData();
  }, []);

  return (
    <LineChart width={1150} height={300} data={performanceData}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="Date" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="PortfolioValue" stroke="#82ca9d" />
    </LineChart>
  );
};

export default SimpleLineChart;
