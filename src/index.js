import React from 'react';
import ReactDOM from 'react-dom';
import App from './component/App';
import './index.css';
import "github-fork-ribbon-css/gh-fork-ribbon.css";

const DEV_URL = 'http://localhost:5000';
const PROD_URL = 'https://playshiritori.com';
const URL = process.env.NODE_ENV === 'development' ? DEV_URL : PROD_URL;
const API_URL = URL + '/api';

ReactDOM.render(<App apiUrl={API_URL}/>, document.getElementById('root'));

