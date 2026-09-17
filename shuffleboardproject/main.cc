#include <iostream>

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


int main() {
    string line1;
    string line2;
    string line3;
    cin >> line1;
    cin >> line2;
    cin >> line3;
    string line = line1+line2+line3;
    cout << "X's index: " <<findx(line) << endl;

    // x's row and col
    int row;
    int col;
    row = findx(line) / 3; // the int make it whole number
    col = findx(line) % 3;
    cout << "X's row: " << row << " X's col: " << col << endl;

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
}


