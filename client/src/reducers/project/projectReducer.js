import {SET_PROJECT_PATH} from "reducers/project/projectActions";

const initialState = {
    path : ""
}

export const projectReducer = (state = initialState, action) => {
    switch(action.type){
        case SET_PROJECT_PATH:
            return {...state, path: action.payload.data}
        default:
            return state
    }
}