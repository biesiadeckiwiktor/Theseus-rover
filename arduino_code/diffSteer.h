#ifndef diffSteer_h
#define diffSteer_h

#include "Arduino.h"

class diffSteer
{
  public:
    diffSteer(float wheelBase, float trackWidth_f, float trackWidth_m, float trackWidth_r);
    void calcSpeed(float speed, float angle, int &fl, int &fr, int &ml, int &mr, int &rl, int &rr);
    void calcSteerAngle(float angle, int &s_fl, int &s_fr, int &s_rl, int &s_rr);
    
  private:
    float _wheelBase;
    float _trackWidth_f;
    float _trackWidth_m;
    float _trackWidth_r;
};

#endif