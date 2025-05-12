#include <bits/stdc++.h>
using namespace std;

string longestCommonPrefix(vector<string>& strs) {
        int n=strs.size();
        if(n==1) return strs[0];
        string sm=strs[0];
        int mins=INT_MAX;
        for(int i=1;i<n;i++){
            int j;
            for(j=0;j<strs[i].size();j++){
                if(sm[j]!=strs[i][j]) {
                    break;
                }
            }
            if(j==0) return "NULL";
            sm=sm.substr(0,j);
        }
        return sm;
    }

int main(){
int n; cin>>n;
vector<string> v(n);
for(int i=0;i<n;i++) cin>>v[i];
cout<<longestCommonPrefix(v);
return 0;
}