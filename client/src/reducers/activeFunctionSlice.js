import {createSlice} from "@reduxjs/toolkit";
import cloneDeep from 'lodash/cloneDeep';

const initialState = {
    activeFunction:{},
};

export const activeFunctionSlice = createSlice({
    name: 'activeFunction',
    initialState: initialState,
    reducers: {
        setActiveFunction: (state, action) => {
            state.activeFunction = cloneDeep(action.payload);
        }
    }
})

export const selectActiveFunction = state => state.activeFunction;
export const {setActiveFunction} = activeFunctionSlice.actions;
export default activeFunctionSlice.reducer;