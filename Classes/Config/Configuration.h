//
//  Configuration.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

#define ICONPOSITION_RIGHT 0
#define ICONPOSITION_LEFT  1

@interface Configuration : NSObject
{
	BOOL showCompleted;
	NSInteger iconPosition;
}

@property (nonatomic, readonly) BOOL showCompleted;
@property (nonatomic, readonly) NSInteger iconPosition;

+ (Configuration *)configuration;

@end
