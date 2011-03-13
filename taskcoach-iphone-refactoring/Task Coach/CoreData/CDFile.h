//
//  CDFile.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 13/03/11.
//  Copyright (c) 2011 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>

@class CDDomainObject;

@interface CDFile : NSManagedObject {
@private
}
@property (nonatomic, retain) NSNumber * endHour;
@property (nonatomic, retain) NSString * name;
@property (nonatomic, retain) NSNumber * startHour;
@property (nonatomic, retain) NSString * guid;
@property (nonatomic, retain) NSSet* objects;

@end
