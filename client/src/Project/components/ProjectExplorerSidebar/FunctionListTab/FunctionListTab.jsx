import React from 'react';

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
        <div className={'function-list-tab'}>
            <table className="table table-hover">
                <thead>
                <tr>
                    <th scope="col">Function Name</th>
                    <th scope="col">File Name</th>
                    <th scope="col">Dependencies</th>
                    <th scope="col">Number of tests</th>
                </tr>
                </thead>
                <tbody>
                {functionList.map(functionInfo => {
                    return (
                        <tr
                            key={functionInfo._id}
                            onClick={() => onClickCallback(functionInfo)}
                            className={isActiveFunction(functionInfo)?"table-active table-primary":""}
                        >
                            <td>{functionInfo.functionId}</td>
                            <td>{functionInfo.fileId}</td>
                            <td>{functionInfo.dependencies}</td>
                            <td>{functionInfo.numberOfTests}</td>
                        </tr>
                    );
                })}
                </tbody>
            </table>
        </div>
    );
}

export default FunctionListTab;