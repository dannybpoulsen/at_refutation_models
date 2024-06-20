
#include <vector>
#include <iostream>

#include <fstream>

enum class  Location {
  I1 = 1,
  I2 = 2,
  I3 = 3,
  I4 = 4,
  I5 = 5,
  I6 = 6,
  I7 = 7,
  I8 = 8,
  I9 = 9,
  L2 = 10,
  L3 = 11,
  L4 = 12,
  L5 = 13,
  L6 = 14,
  L7 = 15
};

enum class  Register {
  a0 = 0,
  a3 = 3,
  a4 = 4,
  a5 = 5
};



inline std::ostream&  operator<< (std::ostream& os, Location l) {
  switch (l) {
  case Location::I1: return os << "I1";
  case Location::I2: return os << "I2";
  case Location::I3: return os << "I3";
  case Location::I4: return os << "I4";
  case Location::I5: return os << "I5";
  case Location::I6: return os << "I6";
  case Location::I7: return os << "I7";
  case Location::I8: return os << "I8";
  case Location::I9: return os << "I9";
  case Location::L2: return os << "L2";
  case Location::L3: return os << "L3";
  case Location::L4: return os << "L4";
  case Location::L5: return os << "L5";
  case Location::L6: return os << "L6";
  case Location::L7: return os << "L7";  
  }
  return os << "?";
}

inline std::ostream&  operator<< (std::ostream& os, Register l) {
  switch (l) {
  case Register::a0: return os << "a0";
  case Register::a3: return os << "a3";
  case Register::a4: return os << "a4";
  case Register::a5: return os << "a5";
  }
  return os << "?";
}


struct Entry {
  Entry (Location loc,Register reg) : flipped_in(loc),reg(reg) {}
  Location flipped_in;
  Register reg;
};



inline std::ostream& operator<< (std::ostream& os, const Entry& en) {
  return os << en.flipped_in<<";"<<en.reg;
}

struct Trace {
  std::vector<Entry> flips;
  void clear () {flips.clear ();}
};

struct GlobalState {
  GlobalState () {
    stream.open ("flip_log", std::fstream::out);
  }
  ~GlobalState () {
    stream.close ();
  }
  std::fstream stream;
  Trace trace;
};

static GlobalState gstate;

extern "C" {

  void new_trace() { gstate.trace.clear(); }
  void save_trace() {
    for (auto& entry : gstate.trace.flips) {
      gstate.stream << entry << ",";
    }
    gstate.stream << std::endl;
  }

  void log_flip (int location,int reg) {
    gstate.trace.flips.push_back ({static_cast<Location> (location),static_cast<Register> (reg)});
  }
  
}





