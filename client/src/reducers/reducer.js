import {combineReducers} from 'redux';
import {projectReducer} from 'reducers/project/projectReducer';
import functionListSlice from "./functionListSlice";
import testListSlice from "./testListSlice";
import activeFunctionSlice from "./activeFunctionSlice";
import activeTestSlice from "./activeTestInfoSlice";

export default combineReducers({
    project : projectReducer,
    functionList: functionListSlice,
    testList: testListSlice,
    activeFunction: activeFunctionSlice,
    activeTest: activeTestSlice,
});