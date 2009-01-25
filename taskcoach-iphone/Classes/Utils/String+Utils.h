//
//  String+Utils.h
//  BookBuddy
//
//  Created by Jérôme Laheurte on 26/12/08.
//  Copyright 2008 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface NSString (Utils)

+ (NSString *)stringFromUTF8Data:(NSData *)data;

// Python's string join-like method
- (NSString *)stringByJoiningStrings:(NSArray *)strings;

@end
