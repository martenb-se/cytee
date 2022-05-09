import React, {useContext} from 'react';
import {selectUnsavedActiveTest, updateReturnValue} from "../../../../reducers/activeTestInfoSlice";
import {useDispatch, useSelector} from "react-redux";

import cloneDeep from "lodash/cloneDeep";

import ArgumentTypeSelector from "../../../../shared/components/ArgumentTypeSelector";
import ArgumentDataFieldInput from "../../../../shared/components/ArgumentInputValueSelector";
import {isEmpty} from "lodash";

import {localTabGroupContext} from "../TestCreatorSection";
import {CollapsibleStateViewer} from "../objectCreationTab/ObjectCreationTab";


function ReturnTab({}) {

    const dispatch = useDispatch();
    const unsavedTest = useSelector(selectUnsavedActiveTest);

    const [, localTabDispatch] = useContext(localTabGroupContext);

    function onChangeCallback(returnValue) {
        dispatch(updateReturnValue(returnValue));
    }

    if (isEmpty(unsavedTest) ||
        (unsavedTest.moduleData === undefined) ||
        (unsavedTest.moduleData.returnValue === undefined)) {
        return <div className="test-creator-tab-empty">waiting...</div>
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
        switch (returnValueClone.type) {
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
                title: "return value - editor"
            }
        });
    }

    return (
        <div className="return-value-tab-wrapper h-100">
            <form
                className="h-100"
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
                {((unsavedTest.moduleData.returnValue.type === 'object') || (unsavedTest.moduleData.returnValue.type === 'array')) &&
                    <CollapsibleStateViewer stateData={unsavedTest.moduleData.returnValue}/>
                }
            </form>
        </div>
    );
}

export default ReturnTab;
