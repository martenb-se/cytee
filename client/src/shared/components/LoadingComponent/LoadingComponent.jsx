import React from 'react';

import {Spinner} from "react-bootstrap";
import './LoadingComponent.scss'

function LoadingComponent(){
    return (
        <div className ="h-100 d-flex align-items-centers justify-content-center">
            <div className="flex d-flex flex-column loading-content">
                <Spinner className="loading-content" animation="border" role="status"></Spinner>
                <span className="loading-content">Loading...</span>
            </div>
        </div>

    );
}

export default LoadingComponent;