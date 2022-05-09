import React, {useState} from 'react';

import {generateTests} from "../../../util/api";
import {useSelector} from "react-redux";
import './GenerateTestsButton.scss'

function GenerateTestsButton() {

    const [generateTestLoading, setGenerateTestLoading] = useState('');
    const projectPath = useSelector(state => state.project.path);

    function generateProjectTests() {
        setGenerateTestLoading('loading');
        generateTests(projectPath).then(() => {
            setGenerateTestLoading('');
        })
    }

    return (
        <button
            className ="generate-tests-button btn btn-primary"
            onClick={() => generateProjectTests()}
            disabled={generateTestLoading !== ''}
        >
            Generate Tests
        </button>
    );

}

export default GenerateTestsButton;