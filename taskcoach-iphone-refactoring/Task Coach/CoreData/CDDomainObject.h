//
//  CDDomainObject.h
//  Task Coach
//
//  Created by Jérôme Laheurte on 13/03/11.
//  Copyright (c) 2011 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>

@class CDFile;

@interface CDDomainObject : NSManagedObject {
@private
}
@property (nonatomic, retain) NSNumber * status;
@property (nonatomic, retain) NSString * name;
@property (nonatomic, retain) NSString * taskCoachId;
@property (nonatomic, retain) CDFile * file;

@end
