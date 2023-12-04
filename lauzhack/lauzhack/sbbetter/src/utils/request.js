
const request = (url, method='GET', body='', callback) => {
    const csrftoken = getCookie("csrftoken");

    let request = method === 'GET' ? new Request(
        url,
        {
            method: method,
            headers: {
                "X-CSRFToken": csrftoken ?? "",
                "Content-Type": "application/json",
            },
        }
    ) : new Request(
        url,
        {
            method: method,
            headers: {
                "X-CSRFToken": csrftoken ?? "",
                "Content-Type": "application/json",
            },
            body: body,
        }
    );


    fetch(request)
        .then((res) => res.json())
        .then((data) => callback(data))
        .catch((err) => console.log(err));
    };

export function getCookie(name) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== "") {
		const cookies = document.cookie.split(";");
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === name + "=") {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

export default request;