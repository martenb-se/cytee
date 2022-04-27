import {createSlice} from "@reduxjs/toolkit";
import cloneDeep from 'lodash/cloneDeep';

const initialState = {
    activeTest: {},
};

export const activeTestSlice = createSlice({
    name: 'activeTest',
    initialState: initialState,
    reducers: {
        setActiveTest: (state, action) => {
            state.activeTest = cloneDeep(action.payload);
        },

        createEmptyActiveTest: (state, action) => {
            const functionInfo = action.payload;
            state.activeTest.activeTest = {
                pathToProject: functionInfo.pathToProject,
                fileId: functionInfo.fileId,
                functionId: functionInfo.functionId,
                customName: "",
                moduleData: {
                    argumentList: [],
                    returnValue: {}
                }
            };
        }
    }
});

export const selectActiveTest = state => state.activeTest;
export const {createEmptyActiveTest} = activeTestSlice.actions;
export default activeTestSlice.reducer;