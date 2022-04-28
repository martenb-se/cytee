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

function TestCreatorPage({}){

    const dispatch = useDispatch();

    const projectPath = useSelector(state => state.project.path);

    const functionListStatus = useSelector(selectFunctionListLoading);
    const functionListError = useSelector(selectFunctionListError);

    const testListStatus = useSelector(selectTestListLoading);
    const testListError = useSelector(selectTestListError);

    const [loadingState, setLoadingState] = useState('');
    const [loadingMessage, setLoadingMessage] = useState('');

    // Load in functions' info
    useEffect(() => {
        setLoadingState('loading');
        setLoadingMessage('Retrieving functions...');
        dispatch(fetchFunctionList(projectPath));
    }, [])

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

    // Load in tests' info
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
        <div className = "test-creator-Page-wrapper">
            <div className = "sidePanel">
                <ProjectExplorerSidebar />
                <button className ="btn btn-primary">Generate Tests</button>
            </div>
            <div className = "testCreationArea">
                <CodeViewingSection />
                <TestCreatorSection />
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