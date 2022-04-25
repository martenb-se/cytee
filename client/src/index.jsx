import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import * as ReactDOMClient from 'react-dom/client';
import {Provider} from 'react-redux';
import store from 'reducers/store'

import App from "./App";

const container = document.getElementById('app');
const root = ReactDOMClient.createRoot(container);
root.render(
    <Provider store={store}>
        <App />
    </Provider>
);
