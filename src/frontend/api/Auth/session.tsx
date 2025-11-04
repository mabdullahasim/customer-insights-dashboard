
export function getToken(): string | null{
    return localStorage.getItem("token");
}

export function checkTokenExpiry(){
    const token = getToken();
    if (token !== null){
        const payload = token.split('.')[1];
        if (payload.length !== 3){
            throw new Error('Invalid jwt format');
        }
        const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
        const {exp} = JSON.parse(atob(base64));

        return Date.now() >= exp *1000;
    }
}

export const isLoggedIn =() =>{
    const token = getToken();
    if (token === null) {
        return false;
    }
    if (!checkTokenExpiry()){
        localStorage.removeItem("token");
        return false;
    }
    return true;
}

