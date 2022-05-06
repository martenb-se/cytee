import {createSlice, createAsyncThunk} from "@reduxjs/toolkit";
import cloneDeep from 'lodash/cloneDeep';
import {editFunctionInfo} from "../util/api";

const initialState = {
    status: "",
    error: "",
    activeFunction:{},
};

export const clearChanges = createAsyncThunk('activeFunction/clearChanges', async ({}, {dispatch, getState}) => {
    const activeFunctionState = cloneDeep(getState().activeFunction.activeFunction);
    activeFunctionState.haveFunctionChanged = false;
    activeFunctionState.changeList = [];
    await editFunctionInfo(activeFunctionState._id, activeFunctionState);
    return activeFunctionState;
})

export const activeFunctionSlice = createSlice({
    name: 'activeFunction',
    initialState: initialState,
    reducers: {
        setActiveFunction: (state, action) => {
            state.activeFunction = cloneDeep(action.payload);
        }
    },
    extraReducers(builder) {
        builder
            .addCase(clearChanges.pending, (state, action) => {
                state.status = 'loading';
            })
            .addCase(clearChanges.fulfilled, (state, action) => {
                state.status = 'succeeded';
                state.activeFunction = action.payload;
            })
            .addCase(clearChanges.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.error.message;
            })
    }
})

export const selectActiveFunction = state => state.activeFunction.activeFunction;
export const selectActiveFunctionLoadingState = state => state.activeFunction.status;
export const {setActiveFunction} = activeFunctionSlice.actions;
export default activeFunctionSlice.reducer;