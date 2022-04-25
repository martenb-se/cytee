export const SET_PROJECT_PATH = "path/set"

export const setPath = (data) => {
    return {
        type: SET_PROJECT_PATH,
        payload: {
            data
        }
    }
}