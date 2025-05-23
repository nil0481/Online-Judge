
import java.lang.*;
import java.util.*;

class Main {

	// Check for number prime or not
	static boolean isPrime(int n)
	{

		// Check if number is less than
		// equal to 1
		if (n <= 1)
			return false;

		// Check if number is 2
		else if (n == 2)
			return true;

		// Check if n is a multiple of 2
		else if (n % 2 == 0)
			return false;

		// If not, then just check the odds
		for (int i = 3; i <= Math.sqrt(n); i += 2) {
			if (n % i == 0)
				return false;
		}
		return true;
	}

	// Driver code
	public static void main(String[] args)
	{
		Scanner scanner = new Scanner(System.in);
	       int n= scanner.nextInt();
		if(isPrime(n))
		System.out.println(1);
		else
		System.out.println(0);
	}
}

