//
//  Configuration.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface Configuration : NSObject
{
	BOOL showCompleted;
}

@property (nonatomic, readonly) BOOL showCompleted;

+ (Configuration *)configuration;

@end
