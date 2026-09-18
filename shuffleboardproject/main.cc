#include <iostream>
#include <queue>
#include <set>

using namespace std;

int findx (string line) {
    
    for (size_t i = 0; i < line.length(); ++i){
        //cout << line << endl;
        if (line[i] == 'x'){
            return i;
        }
    }
    return -1;
}

bool isLegal (char move, int row, int col) {
    if (move == 'u') {
        return row < 2;
    }
    if (move == 'd') {
        return row > 0;
    }
    if (move == 'l') {
        return col < 2;
    }
    if (move == 'r') {
        return col > 0;
    }
    else {
        return false;
    }
}

string movePiece(string line, char move) {
    int newx;
    int xindex = findx(line);

    if (move == 'u') {
        newx = xindex + 3;
    }
    else if (move == 'd') {
        newx = xindex - 3;
    }
    else if (move == 'l') {
        newx = xindex + 1;
    }
    else if (move == 'r') {
        newx = xindex - 1;
    }

    swap(line[xindex], line[newx]);
    return line;
}

struct State {
    string board; //current board state
    string moves; // moves it took to get to current board space
};

int main() {
    string line1;
    string line2;
    string line3;
    cin >> line1;
    cin >> line2;
    cin >> line3;
    string line = line1+line2+line3;
    //cout << line << endl;
    //cout << "X's index: " <<findx(line) << endl;

    // x's row and col
    //int row;
    //int col;
    //row = findx(line) / 3; // the int make it whole number
    //col = findx(line) % 3;
    //cout << "X's row: " << row << " X's col: " << col << endl;

    /*
    //checking legal
    if (isLegal('u', row, col)) {
        cout << "u is legal" << endl;
    }
    if (isLegal('d', row, col)) {
        cout << "d is legal " << endl;
    }
    if (isLegal('l', row, col)) {
        cout << "l is legal" << endl;
    }
    if (isLegal('r', row, col)){
        cout << "r is legal" << endl;
    }
    */

    //checking swapping peice with the x or blank space
    //line = movePiece(line, 'd');
    //cout << line << endl;

    //queue
    string goalBoard = "12345678x";
    //int xindex = findx(line);

    queue<State> q; //board space
    set<string> seen; //boards visited

    q.push({line, ""}); //push the initial board state into the queue
    seen.insert(line); // instert current board as seen

    while (!q.empty()){
        State current = q.front(); //copy first board state to current
        q.pop(); // delete from queue

        //base case
        if (current.board == goalBoard) {
            cout << current.moves << endl;
            return 0;
        }

        //same ones as before finds the index of x and then gives the row and col
        int xindex = findx(current.board); 
        int row = xindex / 3;
        int col = xindex % 3;
        
        string moves = "udlr"; // string of pissible moves
        
        for(size_t i = 0; i < moves.length(); ++i) {
            char move = moves[i];

            if (isLegal(move, row, col)) { //check if move is legal
                string newBoard = movePiece(current.board, move); //making a new board with the move
                if (seen.find(newBoard) == seen.end()) { //make sure new board has not been seeen before
                    seen.insert(newBoard); // mark new board as seen
                    q.push({newBoard, current.moves + move}); //add the board to the queue with the move it took to get there added to all the other moves
                }
            }
        }
    }
    cout << "unsolvable" << endl;
    return 0;
}