import React from 'react';
import {useSelector, useDispatch} from "react-redux";

import {selectTestList} from "../../../../reducers/testListSlice";
import {createEmptyActiveTest} from "../../../../reducers/activeTestInfoSlice";

import CustomTab from "../../../../shared/components/Tab";


function testTabGenerator(){

    const dispatch = useDispatch();
    const testList = useSelector(selectTestList);

    return (
        <CustomTab label='Test Tab'>
            <div>Test Tab</div>
            <table>
                <thead>
                <tr>
                    <th>File Name</th>
                    <th>Function Name</th>
                    <th>Function Description</th>
                </tr>
                </thead>
                <tbody>
                {
                    testList.map(testInfo => {
                        return (
                            <tr key={testInfo._id} onClick={() => {
                                dispatch(setActiveTest(testInfo));
                            }}>
                                <td>{testInfo.fileId}</td>
                                <td>{testInfo.functionId}</td>
                                <td>{testInfo.customName}</td>
                            </tr>
                        )
                    })
                }
                </tbody>
            </table>
        </CustomTab>
    );
}

export default testTabGenerator;