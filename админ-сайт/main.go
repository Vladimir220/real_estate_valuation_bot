package main

import (
	"fmt"
	"html/template"
	"net/http"
)

type PageData struct {
	PageTitle string
}

func main() {

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		tmpl := template.Must(template.ParseFiles(".\\админ-сайт\\frontend\\index.html", ".\\админ-сайт\\frontend\\header.html",
			".\\админ-сайт\\frontend\\footer.html"))
		tmpl.ExecuteTemplate(w, "index", nil)
	})

	fileServer := http.FileServer(http.Dir("./админ-сайт/frontend/"))
	http.Handle("/static/", http.StripPrefix("/static", fileServer))

	http.HandleFunc("/real-estate-models", func(w http.ResponseWriter, r *http.Request) {
		r.ParseForm()
		paramValue := r.FormValue("key")
		if paramValue != "" {
			tmpl := template.Must(template.ParseFiles(".\\админ-сайт\\frontend\\real-estate-models.html", ".\\админ-сайт\\frontend\\header.html",
				".\\админ-сайт\\frontend\\footer.html"))
			data := PageData{PageTitle: paramValue}
			tmpl.ExecuteTemplate(w, "real-estate-models", data)
		} else {
			fmt.Fprintf(w, "No key received")
		}
	})

	http.HandleFunc("/upload", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodPost {
			file, _, err := r.FormFile("file")
			if err != nil {
				http.Error(w, "Ошибка при получении файла", http.StatusBadRequest)
				return
			}
			defer file.Close()

			// Обработка загруженного файла здесь

			w.WriteHeader(http.StatusOK)
			return
		} else {
			http.Error(w, "Метод не поддерживается", http.StatusMethodNotAllowed)
		}
	})

	http.ListenAndServe(":8080", nil)
}
