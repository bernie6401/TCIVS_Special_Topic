String arrivingdatabyte;
int buzzer = 12;
int vibrate = 13;
void setup()
{
  pinMode(vibrate, OUTPUT);
  pinMode(buzzer, OUTPUT);
  Serial.begin(115200);  
}


void loop()
{
  if (Serial.available())
  { 
    arrivingdatabyte = Serial.readStringUntil('\n');
    Serial.print("data byte received:");  
    Serial.println(arrivingdatabyte);

    if(arrivingdatabyte == "Y")
    {
      digitalWrite(buzzer, LOW);
      digitalWrite(vibrate, LOW);
    }
    if(arrivingdatabyte == "V")
    {
      // while(true)
      // {
      digitalWrite(vibrate, HIGH);
      // arrivingdatabyte = Serial.readStringUntil('\n');
      // if(arrivingdatabyte == "Y")
      //   break;
      // }        
    }
    if(arrivingdatabyte == "N")
    {
      digitalWrite(buzzer, HIGH);
    }
  }
}
