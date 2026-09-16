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
int main() {
    string line1;
    string line2;
    string line3;
    cin >> line1;
    cin >> line2;
    cin >> line3;
    string line = line1+line2+line3;
    cout << findx(line) << endl;
}


