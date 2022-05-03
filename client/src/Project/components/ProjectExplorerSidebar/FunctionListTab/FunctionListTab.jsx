import React, {useEffect} from 'react';

import {useSelector, useDispatch} from "react-redux";
import {
    selectFunctionList,
    selectFunctionListError,
    selectFunctionListLoading
} from '../../../../reducers/functionListSlice';
import {selectActiveFunction, setActiveFunction} from "../../../../reducers/activeFunctionSlice";
import {setActiveUnsavedTest, setActiveTest} from "../../../../reducers/activeTestInfoSlice";
import {generateInitTestState} from "../../../../util/generateInitTestState";

import {isEmpty} from "lodash";

import './FunctionListTab.scss'

function fileNameComponent(functionInfo) {

    let resultingFileName;

    if (functionInfo.fileId.indexOf('/') !== -1 ) {
        const splitFileName = functionInfo.fileId.split('/');
        resultingFileName = ((splitFileName.length > 3)?".../":"") + splitFileName[splitFileName.length-2] + '/' + splitFileName[splitFileName.length-1];
    } else {
        resultingFileName = functionInfo.fileId;
    }

    return (
        <td
            className="function-list-tab-file-name-col"
            title={functionInfo.fileId}
        >
            {resultingFileName}
        </td>
    )

}

function functionNameComponent(functionInfo) {
    let resultingFunctionName;

    if (functionInfo.functionId.indexOf('.') !== -1) {
        const splitFunctionName = functionInfo.functionId.split('.');
        resultingFunctionName = ((splitFunctionName.length > 1)?"...":"") + splitFunctionName[splitFunctionName.length-1];
    } else {
        resultingFunctionName = functionInfo.functionId;
    }

    return (
        <td
            className="function-list-tab-function-name-col"
            title={functionInfo.functionId}
        >{resultingFunctionName}</td>
    )
}

function FunctionListTab({label}) {

    const dispatch = useDispatch();

    const functionList = useSelector(selectFunctionList);
    const functionListLoadingState = useSelector(selectFunctionListLoading);
    const functionListErrorMessage = useSelector(selectFunctionListError);

    const activeFunction = useSelector(selectActiveFunction);

    function isActiveFunction(funcInfo) {
        return (!isEmpty(activeFunction)) &&
            (activeFunction.pathToProject === funcInfo.pathToProject) &&
            (activeFunction.fileId === funcInfo.fileId) &&
            (activeFunction.functionId === funcInfo.functionId);
    }

    function onClickCallback(functionInfo) {
        dispatch(setActiveFunction(functionInfo));
        dispatch(setActiveUnsavedTest({
            customName: "",
            moduleData: generateInitTestState(),
        }));
        dispatch(setActiveTest({}));
    }

    if ((functionListLoadingState === 'loading') ||
        (functionListLoadingState === '')) {
        return <div>Fetching Functions....</div>
    }

    if (functionListLoadingState === 'failed'){
        return (
            <>
                <div>Error</div>
                <span>{functionListErrorMessage}</span>
            </>
        );
    }

    return (
        <div className='function-list-tab'>

            <table className="table table-hover function-list-tab-table">
                <thead>
                <tr>
                    <th scope="col">Function Name</th>
                    <th  scope="col">File Name</th>
                    <th
                        className="function-list-tab-dependencies-col"
                        scope="col">
                        Dependencies
                    </th>
                    <th
                        className="function-list-tab-number-of-test-col"
                        scope="col">
                        Number of tests
                    </th>
                    <th>
                        Have Function Changed
                    </th>
                </tr>
                </thead>
                <tbody>
                {functionList.map(functionInfo => {
                    return (
                        <tr
                            key={functionInfo._id}
                            onClick={() => onClickCallback(functionInfo)}
                            data-bs-toggle="modal"
                            data-bs-target="#staticBackdrop"
                            className={
                                (isActiveFunction(functionInfo)?"table-active":"") + " "
                            }
                        >
                            {functionNameComponent(functionInfo)}
                            {fileNameComponent(functionInfo)}
                            <td
                                className="function-list-tab-dependencies-col"
                            >{functionInfo.dependencies}</td>
                            <td
                                className="function-list-tab-number-of-test-col"
                            >{functionInfo.numberOfTests}</td>
                            <td>
                                <span
                                    className={(functionInfo.haveFunctionChanged)?"badge bg-warning":"badge bg-success"}
                                >
                                    {(functionInfo.haveFunctionChanged)?"Has been Altered":"Up To Date" }
                                </span>
                            </td>

                        </tr>
                    );
                })}
                </tbody>
            </table>
        </div>
    );
}

export default FunctionListTab;