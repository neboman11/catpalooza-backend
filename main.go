package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"time"

	mysql "github.com/go-sql-driver/mysql"
	"github.com/gorilla/mux"
)

const databaseUser = "catpalooza"
const databasePassword = "catpalooza"
const databaseHost = "www.nesbitt.rocks"
const databaseName = "catpalooza"
const databaseTable = "photos"
const photoSQLQuery = "SELECT * FROM " + databaseTable + " WHERE id = "
const rowCountSQLQuery = `SELECT COUNT(id) FROM photos;`
const connectionTimeoutLength = 3 // minutes

var db *sql.DB // Database connection pool.

type databaseRow struct {
	ID    int    `json:"id"`
	Name  string `json:"name"`
	Photo []byte `json:"photo"`
	Size  uint32 `json:"size"`
	Score int    `json:"score"`
}

func main() {
	setupDatabaseConnection()
	handleRequests()
}

func setupDatabaseConnection() {
	config := mysql.Config{
		User:                 databaseUser,
		Passwd:               databasePassword,
		Net:                  "tcp",
		Addr:                 databaseHost,
		DBName:               databaseName,
		AllowNativePasswords: true,
	}
	configString := config.FormatDSN()
	var err error
	db, err = sql.Open("mysql", configString)
	if err != nil {
		fmt.Printf("Failed to connect to database: %s", err)
		return
	}
	// See "Important settings" section.
	db.SetConnMaxLifetime(time.Minute * connectionTimeoutLength)
	db.SetMaxOpenConns(20)
	db.SetMaxIdleConns(20)
}

func handleRequests() {
	myRouter := mux.NewRouter().StrictSlash(true)

	// GETs
	myRouter.HandleFunc("/", homePage)
	myRouter.HandleFunc("/random", getRandomPicture)
	myRouter.HandleFunc("/score", scorePhoto)

	log.Fatal(http.ListenAndServe(":10000", myRouter))
}

func homePage(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Welcome to the Home Page!")
}

func getRandomPicture(w http.ResponseWriter, r *http.Request) {
	photo, err := queryPhoto(r.Context())
	if err != nil {
		fmt.Fprintf(w, "Failed to query database: %s", err)
		return
	}

	body, err := json.Marshal(photo)
	w.Header().Add("Access-Control-Allow-Origin", "*")
	fmt.Fprintf(w, "%s", body)
}

func queryPhoto(ctx context.Context) (databaseRow, error) {
	var photo databaseRow
	var rowCount int
	response := db.QueryRowContext(ctx, rowCountSQLQuery)
	err := response.Scan(&rowCount)
	if err != nil {
		return photo, err
	}

	randomRow := rand.Int() % rowCount

	response = db.QueryRowContext(ctx, photoSQLQuery+fmt.Sprintf("%d;", randomRow))
	err = response.Scan(&photo.ID, &photo.Name, &photo.Photo, &photo.Size, &photo.Score)
	if err != nil {
		return photo, err
	}
	return photo, nil
}

func scorePhoto(w http.ResponseWriter, r *http.Request) {
	keys := r.URL.Query()

	if len(keys) != 2 {
		fmt.Fprintf(w, "Invalid number of url parameters!")
		return
	}

	id, ok := keys["id"]
	if !ok {
		fmt.Fprintf(w, "Missing 'id' parameter")
		return
	}

	score, ok := keys["score"]
	if !ok {
		fmt.Fprintf(w, "Missing 'score' parameter")
		return
	}

	UpdateSQLQuery := "UPDATE " + databaseTable + " SET score = " + score[0] + " WHERE id = " + id[0] + ";"

	response := db.QueryRowContext(r.Context(), UpdateSQLQuery)
	err := response.Scan()
	if err != nil {
		fmt.Fprintf(w, "Failed to update database: %s", err)
	}

	return
}
