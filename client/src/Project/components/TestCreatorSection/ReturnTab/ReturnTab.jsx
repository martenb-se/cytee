import React, {useContext} from 'react';
import {selectUnsavedActiveTest, updateReturnValue} from "../../../../reducers/activeTestInfoSlice";
import {useDispatch, useSelector} from "react-redux";

import cloneDeep from "lodash/cloneDeep";

import ArgumentTypeSelector from "../../../../shared/components/ArgumentTypeSelector";
import ArgumentDataFieldInput from "../../../../shared/components/ArgumentInputValueSelector";
import {isEmpty} from "lodash";

import {localTabGroupContext} from "../TestCreatorTabGroup/TestCreatorTabGroup";
import {CollapsibleStateViewer} from "../objectCreationTab/ObjectCreationTab";


function ReturnTab({label}) {

    const dispatch = useDispatch();
    const unsavedTest = useSelector(selectUnsavedActiveTest);

    const [localTabState, localTabDispatch] = useContext(localTabGroupContext);

    function onChangeCallback(returnValue) {
        dispatch(updateReturnValue(returnValue));
    }

    if (isEmpty(unsavedTest) ||
        (unsavedTest.moduleData === undefined) ||
        (unsavedTest.moduleData.returnValue === undefined)) {
        return <div className ="test-creator-tab-empty">waiting...</div>
    }

    function changeReturnValueTypeCallback(e, returnValueData) {
        const returnValueClone = cloneDeep(unsavedTest.moduleData.returnValue);
        if ((returnValueClone.type === 'object') || (returnValueClone.type === 'array')) {
            localTabDispatch({
                type: 'removeChildTab',
                payload: returnValueData.argument,
            });
        }
        returnValueClone.type = e.target.value;
        switch(returnValueClone.type) {
            case 'undefined':
            case 'null':
                delete returnValueClone.value;
                break;
            case 'array':
                returnValueClone.value = [];
                break;
            case 'boolean':
                returnValueClone.value = false;
                break;
            case 'number':
                returnValueClone.value = 0;
                break;
            case 'string':
                returnValueClone.value = '';
                break;
            case 'object':
                returnValueClone.value = [];
                break;
        }

        onChangeCallback(returnValueClone);
    }

    function changeReturnValueCallback(e) {
        e.preventDefault();
        const returnValueClone = cloneDeep(unsavedTest.moduleData.returnValue);
        returnValueClone.value = e.target.value;
        onChangeCallback(returnValueClone);
    }

    function onSubTabChangeCallback(objectData) {
        const argumentDataClone = cloneDeep(objectData);
        localTabDispatch({
            type: 'removeChildTab',
            payload: 'returnValueChild'
        });
        onChangeCallback(argumentDataClone);
    }

    function onEdit(returnValueData) {
        const returnValueDataClone = cloneDeep(returnValueData);
        returnValueDataClone['argument'] = 'returnValue';
        localTabDispatch({
            type: 'addChildTab',
            payload: {
                initValue: returnValueDataClone,
                onObjectChangeCallback: onSubTabChangeCallback,
                parentEventKey: "returnValue",
                eventKey: 'returnValueChild',
                title:  "return value - editor"
            }
        });
    }

    return (
            <div className="return-value-tab-wrapper">
                <form
                    onSubmit={e => e.preventDefault()}
                >
                    <label
                        className="form-label"
                        htmlFor={"return-value-tab-type-field"}
                    >
                        Return Value
                    </label>
                    <div className="input-group">
                        <ArgumentTypeSelector
                            id={"return-value-tab-type-field"}
                            type={unsavedTest.moduleData.returnValue.type}
                            onChangeCallback={changeReturnValueTypeCallback}
                        />
                        <ArgumentDataFieldInput
                            argumentData={unsavedTest.moduleData.returnValue}
                            onChangeCallback={changeReturnValueCallback}
                            disabled={false}
                            onEdit={onEdit}
                        />
                    </div>
                    {(unsavedTest.moduleData.returnValue.type === 'object') &&
                        <CollapsibleStateViewer stateData={unsavedTest.moduleData.returnValue}/>
                    }
                </form>
            </div>
    );
}

export default ReturnTab;

/*
import React, {useContext, useEffect} from 'react';

// lodash helpers
import cloneDeep from "lodash/cloneDeep";

// components
import CustomTab from "../../../../shared/components/Tab";
import ArgumentTypeSelector from "../../../../shared/components/ArgumentTypeSelector";
import ArgumentDataFieldInput from "../../../../shared/components/ArgumentInputValueSelector";

import {unsavedTestInfoContext} from "../TestCreatorSection";

function returnTabGenerator() {

    const [state, dispatch] = useContext(unsavedTestInfoContext);

    useEffect(() => {
        console.log('state: ', state);
    }, [state])

    function changeReturnValueTypeCallback(e) {
        const returnValueClone = cloneDeep(state.moduleData.returnValue);
        returnValueClone.type = e.target.value;
        switch(returnValueClone.type) {
            case 'undefined':
            case 'null':
                delete returnValueClone.value;
                break;
            case 'array':
                returnValueClone.value = [];
                break;
            case 'boolean':
                returnValueClone.value = false;
                break;
            case 'number':
                returnValueClone.value = 0;
                break;
            case 'string':
                returnValueClone.value = '';
                break;
            case 'object':
                returnValueClone.value = {};
                break;
        }

        dispatch({
            type: 'returnValue/updateReturnValue',
            payload: returnValueClone,
        })
    }

    function changeReturnValueCallback(e) {
        const returnValueClone = cloneDeep(state.moduleData.returnValue);
        returnValueClone.value = e.target.value;
        dispatch({
            type: 'returnValue/updateReturnValue',
            payload: returnValueClone,
        })
    }

    return (
       <CustomTab label='Return value'>
           <div>
               <h1>Return Value Tab</h1>
               <div>
                   <span>Return Value</span>
                   <ArgumentTypeSelector
                       type={state.moduleData.returnValue.type}
                       onChangeCallback={changeReturnValueTypeCallback}
                   />
                   <ArgumentDataFieldInput
                       type={state.moduleData.returnValue.type}
                       value={state.moduleData.returnValue.value}
                       onChangeCallback={changeReturnValueCallback}
                   />
               </div>
           </div>
       </CustomTab>
    );
}

export default returnTabGenerator;

 */