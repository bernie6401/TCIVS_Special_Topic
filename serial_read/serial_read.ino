// the setup function runs once when you press reset or power the board
int arrivingdatabyte;
void setup()
{
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);  
}

// the loop function runs over and over again forever
void loop()
{
  if (Serial.available( ) > 0)
  {
    arrivingdatabyte = Serial.read();  // It will read the incoming or arriving data byte  
    Serial.print("data byte received:");  
    Serial.println(arrivingdatabyte);  
  }
//  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
//  delay(1000);                       // wait for a second
//  digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
//  delay(1000);                       // wait for a second
}
