//
//  DomainObject.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

#define STATUS_NONE               0
#define STATUS_NEW                1
#define STATUS_MODIFIED           2
#define STATUS_DELETED            3

@interface DomainObject : NSObject
{
	NSInteger objectId;
	NSString *name;
	NSInteger status;
}

@property (nonatomic, readonly) NSInteger objectId;
@property (nonatomic, retain) NSString *name;
@property (nonatomic, readonly) NSInteger status;

- initWithId:(NSInteger)ID name:(NSString *)name status:(NSInteger)status;

- (void)setStatus:(NSInteger)status;

@end
