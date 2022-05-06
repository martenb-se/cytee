import React, {useState, useEffect} from 'react';
import './TestCreatorPage.scss';

import ProjectExplorerSidebar from '../../components/ProjectExplorerSidebar'
import CodeViewingSection from "../../components/CodeViewerSection";
import TestCreatorSection from "../../components/TestCreatorSection";

import {useSelector, useDispatch} from "react-redux";
import {
    selectFunctionListLoading,
    selectFunctionListError,
    fetchFunctionList
} from "../../../reducers/functionListSlice";
import {
    selectTestListLoading,
    selectTestListError,
    fetchTestList
} from "../../../reducers/testListSlice";

import {generateTests, removeChangesFromUntestedFunctions} from "../../../util/api";

function TestCreatorPage({}){

    const dispatch = useDispatch();

    const projectPath = useSelector(state => state.project.path);

    const functionListStatus = useSelector(selectFunctionListLoading);
    const functionListError = useSelector(selectFunctionListError);

    const testListStatus = useSelector(selectTestListLoading);
    const testListError = useSelector(selectTestListError);

    const [loadingClearingSate, setLoadingClearingState] = useState('');
    const [loadingState, setLoadingState] = useState('');
    const [loadingMessage, setLoadingMessage] = useState('');

    const [generateTestLoading, setGenerateTestLoading] = useState('');

    useEffect(() => {
        setLoadingClearingState('loading');
        removeChangesFromUntestedFunctions(projectPath).then(data => {
            setLoadingClearingState('succeeded')
        });
    }, [])

    // Load in functions' info
    useEffect(() => {
        if (loadingState !== 'loading') {
            if (loadingClearingSate === 'succeeded') {
                setLoadingState('loading');
                setLoadingMessage('Retrieving functions...');
                dispatch(fetchFunctionList(projectPath));
            }
        }
    }, [loadingClearingSate])

    useEffect(() => {
        if (loadingState !== 'done') {
            if (functionListStatus === 'succeeded') {
                setLoadingMessage('Retrieving tests...');
                dispatch(fetchTestList(projectPath));

            } else if (functionListStatus === 'failed') {
                setLoadingState('failed');
                setLoadingMessage(functionListError);
            }
        }
    }, [functionListStatus])

    useEffect(() => {
        if (loadingState !== 'done') {
            if (testListStatus === 'succeeded') {
                setLoadingState('done');
                setLoadingMessage('');
            } else if (testListStatus === 'failed') {
                setLoadingState('failed');
                setLoadingMessage(testListError);
            }
        }
    }, [testListStatus]);

    if (loadingState === 'failed') {
        return (
            <ErrorScreen errorMessage={loadingMessage} />
        );
    }

    if (loadingState !== 'done') {
        return (
                <LoadingScreen loadingMessage={loadingMessage}/>
        );
    }

    return (
        <div className = "container-fluid test-creator-Page-wrapper">
            <div className ="row">
                <div className = "test-creator-side-panel col-auto">
                    <ProjectExplorerSidebar />
                </div>
                <div className = "test-creation-area col">
                    <CodeViewingSection/>
                    <TestCreatorSection/>
                </div>
            </div>
        </div>
    );
}

function LoadingScreen({loadingMessage}) {
    return (
        <div className='loadingScreen'>
            <h1 className='loadingScreen-header'>Loading...</h1>
            <span className='loadingScreen-content'>{loadingMessage}</span>
        </div>
    )
}

function ErrorScreen({errorMessage}) {
    return (
        <div className='ErrorScreen'>
            <h1 className='ErrorScreen-header'>An Error Occurred!</h1>
            <span className='errorScreen-content'>{errorMessage}</span>
        </div>
    )
}

export default TestCreatorPage;